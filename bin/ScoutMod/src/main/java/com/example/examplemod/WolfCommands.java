package com.example.examplemod;

import net.minecraft.entity.Entity;
import net.minecraft.entity.ai.EntityAIBase;
import net.minecraft.entity.ai.EntityAIFollowOwner;
import net.minecraft.entity.ai.EntityAITasks.EntityAITaskEntry;
import net.minecraft.entity.passive.EntityWolf; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/passive/EntityWolf.html)
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraft.world.World; 


import net.minecraft.pathfinding.PathNavigate;

import net.minecraft.entity.player.EntityPlayer;

import java.util.*;


public class WolfCommands {

    public static EntityWolf getSpecificWolf(String name, World world) {
        EntityWolf wolf = null;
        List<Entity> entityList = world.getLoadedEntityList();
        for (Entity ent : entityList) {
            if (ent instanceof EntityWolf && 
                ent.hasCustomName() &&
                ent.getCustomNameTag() == name) {
                System.out.format("Found %s\n", ent.getCustomNameTag());
                wolf = (EntityWolf) ent;
                break;
            }
        }
        return wolf;
    }

    public static void removeAllTasks(EntityWolf wolf) {
        for (Object a : wolf.tasks.taskEntries.toArray()) {
                EntityAIBase task = ((EntityAITaskEntry) a).action;           
                System.out.format("Removed task from wolf\n");
                wolf.tasks.removeTask(task);
            }
    }

    public static void followPlayer(EntityWolf wolf) {
        System.out.format("[COMMAND] followPlayer executing\n");
        // WolfCommands.removeAllTasks(wolf);
        // wolf.tasks.addTask(0, EntityAIFollowOwner(wolf, );
        
        // tryMoveToEntityLiving(Entity entityIn, double speedIn) 
        wolf.setSitting(false); // mob cannot follow if sitting
        // wolf.getNavigation().a()
    }

    public static void sit(EntityWolf wolf) {
        wolf.setSitting(true);
    }
}