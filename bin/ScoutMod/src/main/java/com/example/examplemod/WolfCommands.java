package com.example.examplemod;

import net.minecraft.entity.Entity;
import net.minecraft.entity.ai.EntityAIBase;
import net.minecraft.entity.ai.EntityAISit;
import net.minecraft.entity.ai.EntityAIFollowOwner;
import net.minecraft.entity.ai.EntityAITasks.EntityAITaskEntry;

import net.minecraft.entity.passive.EntityTameable;
import net.minecraft.entity.passive.EntityWolf; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/passive/EntityWolf.html)
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraft.world.World; 
import net.minecraft.pathfinding.PathNavigate;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.util.math.RayTraceResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.client.Minecraft;

import java.util.*;


public class WolfCommands {

    public static EntityWolf getSpecificWolf(String name, World world) {
        System.out.format("[WOLFCOMMANDS] getSpecificWolf executing\n");
        EntityWolf wolf = null;
        List<Entity> entityList = world.getLoadedEntityList();
        for (Entity ent : entityList) {
            if (ent instanceof EntityWolf) {   
                System.out.format("\tExamining %s\n", ent.getName());
                System.out.format("\thasCustomName: %b, getCustomNameTag: %s\n", 
                                    ent.hasCustomName(), 
                                    ent.getCustomNameTag());
            }


            if (ent instanceof EntityWolf && 
                ent.hasCustomName() &&
                name.equals(ent.getCustomNameTag()) ) {
                System.out.format("[WOLFCOMMANDS] Found %s\n", ent.getCustomNameTag());
                wolf = (EntityWolf) ent;
                break;
            }
        }
        return wolf;
    }

    public static void removeAllTasks(EntityWolf wolf) {
        for (Object a : wolf.tasks.taskEntries.toArray()) {
                EntityAIBase task = ((EntityAITaskEntry) a).action;           
                System.out.format("[WOLFCOMMANDS] Removed task from wolf\n");
                wolf.tasks.removeTask(task);
            }
    }

    public static void followPlayer(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] followPlayer executing\n");
        // WolfCommands.removeAllTasks(wolf);
        // wolf.tasks.addTask(0, EntityAIFollowOwner(wolf, );
        
        // tryMoveToEntityLiving(Entity entityIn, double speedIn) 
        wolf.getAISit().setSitting(false);
        // wolf.getNavigation().a()
    }

    public static void sit(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] sit executing\n");
        wolf.getAISit().setSitting(true);
    }

    public static void goToWhereUserIsLooking(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] goToWhereUserIsLooking executing\n");
        RayTraceResult mop = Minecraft.getMinecraft().getRenderViewEntity().rayTrace(200, 1.0F);

        if (mop != null)
        {
            BlockPos blockPos = mop.getBlockPos(); 
            System.out.format("\tRaytrace hit Block at {%d %d %d}\n", blockPos.getX(), blockPos.getY(), blockPos.getZ());
            
            // disable user following
            
            // move to location
            PathNavigate nav = wolf.getNavigator();
            boolean result = nav.tryMoveToXYZ(blockPos.getX(), blockPos.getY(), blockPos.getZ(), 1.0F);
            System.out.format("\tWolf can move to location: {%b}\n", result);
        }
    }
}